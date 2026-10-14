"use client";

import { useCallback, useEffect, useState } from "react";

import { NOTIFICATION_POLL_MS } from "@/lib/notification-inbox";
import type { InboxNotification } from "@/lib/notification-inbox";
import {
  getNotificationUnreadCount,
  listNotificationInbox,
  markAllNotificationsRead,
  markNotificationRead,
} from "@/services/notification-inbox-service";

type InboxState = {
  items: InboxNotification[];
  unreadCount: number;
  loading: boolean;
  error: string | null;
};

const initialState: InboxState = {
  items: [],
  unreadCount: 0,
  loading: true,
  error: null,
};

export function useNotificationInbox(options?: { enabled?: boolean }) {
  const enabled = options?.enabled ?? true;
  const [state, setState] = useState<InboxState>(
    enabled ? initialState : { ...initialState, loading: false },
  );

  const refresh = useCallback(async () => {
    if (!enabled) return;
    try {
      const [items, unreadCount] = await Promise.all([
        listNotificationInbox(),
        getNotificationUnreadCount(),
      ]);
      setState({
        items,
        unreadCount,
        loading: false,
        error: null,
      });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Unable to load notifications";
      setState((prev) => ({
        ...prev,
        loading: false,
        error: message,
      }));
    }
  }, [enabled]);

  useEffect(() => {
    if (!enabled) {
      setState({ items: [], unreadCount: 0, loading: false, error: null });
      return;
    }

    let active = true;

    async function load() {
      try {
        const [items, unreadCount] = await Promise.all([
          listNotificationInbox(),
          getNotificationUnreadCount(),
        ]);
        if (!active) return;
        setState({ items, unreadCount, loading: false, error: null });
      } catch (error) {
        if (!active) return;
        const message = error instanceof Error ? error.message : "Unable to load notifications";
        setState((prev) => ({ ...prev, loading: false, error: message }));
      }
    }

    void load();
    const intervalId = window.setInterval(() => {
      void load();
    }, NOTIFICATION_POLL_MS);

    function onFocus() {
      void load();
    }
    window.addEventListener("focus", onFocus);

    return () => {
      active = false;
      window.clearInterval(intervalId);
      window.removeEventListener("focus", onFocus);
    };
  }, [enabled]);

  const markRead = useCallback(async (id: string) => {
    setState((prev) => {
      const items = prev.items.map((item) =>
        item.id === id ? { ...item, unread: false, read_at: item.read_at ?? new Date().toISOString() } : item,
      );
      return {
        ...prev,
        items,
        unreadCount: items.filter((item) => item.unread).length,
      };
    });
    try {
      await markNotificationRead(id);
    } catch {
      // Keep optimistic read state; next poll will reconcile.
    }
  }, []);

  const markAllRead = useCallback(async () => {
    setState((prev) => ({
      ...prev,
      items: prev.items.map((item) => ({
        ...item,
        unread: false,
        read_at: item.read_at ?? new Date().toISOString(),
      })),
      unreadCount: 0,
    }));
    try {
      await markAllNotificationsRead();
    } catch {
      // Keep optimistic read state; next poll will reconcile.
    }
  }, []);

  return {
    ...state,
    refresh,
    markRead,
    markAllRead,
  };
}
