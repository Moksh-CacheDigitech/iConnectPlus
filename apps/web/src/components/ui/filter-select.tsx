"use client";

import { useCallback, useEffect, useId, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { ChevronDown } from "lucide-react";

import { cn } from "@/lib/utils";

export type FilterSelectOption = {
  value: string;
  label: string;
};

type FilterSelectProps = {
  value: string;
  onChange: (value: string) => void;
  options: FilterSelectOption[];
  /** Shown for empty value (e.g. "All") */
  placeholder?: string;
  className?: string;
  disabled?: boolean;
};

/**
 * Filter dropdown matching CRM popovers
 * (`rounded-lg border border-border bg-popover shadow-md`).
 */
export function FilterSelect({
  value,
  onChange,
  options,
  placeholder = "All",
  className,
  disabled,
}: FilterSelectProps) {
  const listId = useId();
  const triggerRef = useRef<HTMLButtonElement>(null);
  const menuRef = useRef<HTMLUListElement>(null);
  const [open, setOpen] = useState(false);
  const [mounted, setMounted] = useState(false);
  const [coords, setCoords] = useState<{
    top: number;
    left: number;
    width: number;
  } | null>(null);

  const selected = options.find((o) => o.value === value);
  const label = selected?.label || placeholder;

  useEffect(() => {
    setMounted(true);
  }, []);

  const updatePosition = useCallback(() => {
    const trigger = triggerRef.current;
    if (!trigger) return;
    const rect = trigger.getBoundingClientRect();
    const menu = menuRef.current;
    const menuHeight = menu?.offsetHeight || 220;
    const gap = 4;
    const pad = 8;

    let top = rect.bottom + gap;
    if (top + menuHeight > window.innerHeight - pad) {
      top = Math.max(pad, rect.top - gap - menuHeight);
    }

    const width = Math.min(Math.max(rect.width, 180), window.innerWidth - pad * 2);
    let left = rect.left;
    left = Math.min(Math.max(pad, left), window.innerWidth - width - pad);
    setCoords({ top, left, width });
  }, []);

  useLayoutEffect(() => {
    if (!open) {
      setCoords(null);
      return;
    }
    updatePosition();
    const id = requestAnimationFrame(() => updatePosition());
    return () => cancelAnimationFrame(id);
  }, [open, updatePosition, options.length]);

  useEffect(() => {
    if (!open) return;

    function onDoc(e: MouseEvent) {
      const t = e.target as Node;
      if (triggerRef.current?.contains(t) || menuRef.current?.contains(t)) return;
      setOpen(false);
    }
    function onKey(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
    }

    document.addEventListener("mousedown", onDoc);
    document.addEventListener("keydown", onKey);
    window.addEventListener("resize", updatePosition);
    window.addEventListener("scroll", updatePosition, true);
    return () => {
      document.removeEventListener("mousedown", onDoc);
      document.removeEventListener("keydown", onKey);
      window.removeEventListener("resize", updatePosition);
      window.removeEventListener("scroll", updatePosition, true);
    };
  }, [open, updatePosition]);

  return (
    <div className={cn("relative min-w-0", className)}>
      <button
        ref={triggerRef}
        type="button"
        disabled={disabled}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={open ? listId : undefined}
        title={label}
        className={cn(
          "flex h-8.5 w-full cursor-pointer items-center justify-between gap-2 rounded-lg border border-input/80 bg-background/60 px-3 text-left text-sm outline-none transition-all duration-150",
          "hover:bg-muted/20",
          "focus-visible:border-primary/60 focus-visible:ring-3 focus-visible:ring-primary/15",
          "shadow-[0_1px_2px_0_rgba(0,0,0,0.02)] backdrop-blur-xs",
          open && "border-ring ring-3 ring-ring/50",
          "disabled:cursor-not-allowed disabled:opacity-50",
        )}
        onClick={() => setOpen((v) => !v)}
      >
        <span className={cn("min-w-0 truncate", !selected && "text-muted-foreground")}>{label}</span>
        <ChevronDown
          className={cn(
            "size-4 shrink-0 text-muted-foreground transition-transform duration-200",
            open && "rotate-180",
          )}
        />
      </button>

      {mounted && open
        ? createPortal(
          <ul
            ref={menuRef}
            id={listId}
            role="listbox"
            aria-label={placeholder}
            className="fixed z-[200] max-h-48 overflow-y-auto rounded-lg border border-border bg-popover py-1 shadow-md"
            style={{
              top: coords?.top ?? 0,
              left: coords?.left ?? 0,
              width: coords?.width ?? 180,
              visibility: coords ? "visible" : "hidden",
            }}
          >
            {options.map((opt) => {
              const active = opt.value === value;
              return (
                <li key={opt.value || "__all__"}>
                  <button
                    type="button"
                    role="option"
                    aria-selected={active}
                    title={opt.label}
                    className={cn(
                      "w-full cursor-pointer px-3 py-1.5 text-left text-sm transition-colors duration-200 hover:bg-muted/80",
                      active && "bg-muted/60 font-medium",
                    )}
                    onMouseDown={(e) => e.preventDefault()}
                    onClick={() => {
                      onChange(opt.value);
                      setOpen(false);
                    }}
                  >
                    {opt.label}
                  </button>
                </li>
              );
            })}
          </ul>,
          document.body,
        )
        : null}
    </div>
  );
}
