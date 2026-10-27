"use client";

import { useMemo } from "react";

import { SearchableSelect } from "@/components/ui/searchable-select";
import { erpModules } from "@/config/modules";
import { cn } from "@/lib/utils";

/** Sentinel value for Organization → Users “All modules” entitlement. */
export const ALL_MODULES_KEY = "*";

/** Platform / shell modules — not offered in Organization → Users assign picker. */
export const NON_ASSIGNABLE_MODULE_KEYS = new Set([
  "foundation",
  "email",
  "voice-agent",
  "organization",
  "master-data",
]);

type Props = {
  id?: string;
  value: string;
  onChange: (moduleKey: string) => void;
  disabled?: boolean;
  className?: string;
};

/** Module picker — CRM popover style (search + title / description rows). */
export function ModuleAssignSelect({ id: _id, value, onChange, disabled, className }: Props) {
  const options = useMemo(
    () => [
      {
        value: ALL_MODULES_KEY,
        label: "All modules",
        description:
          "Full module-admin access across every ERP module (not the same as ERP admin).",
      },
      ...erpModules
        .filter((m) => !NON_ASSIGNABLE_MODULE_KEYS.has(m.key))
        .map((m) => ({
          value: m.key,
          label: m.title,
          description: m.description,
        })),
    ],
    [],
  );

  return (
    <SearchableSelect
      value={value}
      onChange={onChange}
      options={options}
      placeholder="Select module…"
      searchPlaceholder="Search modules…"
      disabled={disabled}
      className={cn(className)}
      allowCustomValue={false}
      searchable
    />
  );
}
