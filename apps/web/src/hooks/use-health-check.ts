"use client";

import { useCallback, useEffect, useState } from "react";

import { ApiClientError, healthService } from "@/services/api-client";
import type { HealthData } from "@/types/api";

interface HealthState {
  data: HealthData | null;
  loading: boolean;
  error: string | null;
}

const initialState: HealthState = {
  data: null,
  loading: true,
  error: null,
};

export function useHealthCheck() {
  const [state, setState] = useState<HealthState>(initialState);

  const refresh = useCallback(async () => {
    setState((prev) => ({ ...prev, loading: true, error: null }));
    try {
      const response = await healthService.check();
      setState({
        loading: false,
        error: null,
        data: (response.data as HealthData | null) ?? null,
      });
    } catch (error) {
      const message =
        error instanceof ApiClientError ? error.message : "Unable to reach API";
      setState({ loading: false, error: message, data: null });
    }
  }, []);

  useEffect(() => {
    let active = true;

    async function loadHealth() {
      setState((prev) => ({ ...prev, loading: true, error: null }));
      try {
        const response = await healthService.check();
        if (!active) return;
        setState({
          loading: false,
          error: null,
          data: (response.data as HealthData | null) ?? null,
        });
      } catch (error) {
        if (!active) return;
        const message =
          error instanceof ApiClientError ? error.message : "Unable to reach API";
        setState({ loading: false, error: message, data: null });
      }
    }

    void loadHealth();

    return () => {
      active = false;
    };
  }, []);

  return { ...state, refresh };
}
