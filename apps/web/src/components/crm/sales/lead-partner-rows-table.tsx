"use client";

import type { LucideIcon } from "lucide-react";
import { Plus, Trash2 } from "lucide-react";

import { CRM_TABLE_HEAD_CELL, CRM_TABLE_HEAD_ROW, CrmSection } from "@/components/crm/crm-ui";
import { FinanceSelect } from "@/components/finance/journals/finance-form-field";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  emptyLeadPartnerRow,
  type LeadPartnerRow,
} from "@/lib/crm/lead-partner-rows";
import { cn } from "@/lib/utils";

type LeadPartnerRowsTableProps = {
  title: string;
  icon: LucideIcon;
  nameLabel: string;
  rows: LeadPartnerRow[];
  nameOptions: readonly string[];
  onChange: (rows: LeadPartnerRow[]) => void;
  nameRequired?: boolean;
  /** Allow typing a name not in the preset list (distributors). */
  allowCustomName?: boolean;
};

export function LeadPartnerRowsTable({
  title,
  icon,
  nameLabel,
  rows,
  nameOptions,
  onChange,
  nameRequired = false,
  allowCustomName = false,
}: LeadPartnerRowsTableProps) {
  const displayRows = rows.length > 0 ? rows : [emptyLeadPartnerRow()];

  function updateRow(id: string, patch: Partial<LeadPartnerRow>) {
    onChange(displayRows.map((row) => (row.id === id ? { ...row, ...patch } : row)));
  }

  function addRow() {
    onChange([...displayRows, emptyLeadPartnerRow()]);
  }

  function removeRow(id: string) {
    if (displayRows.length <= 1) {
      onChange([emptyLeadPartnerRow()]);
      return;
    }
    onChange(displayRows.filter((row) => row.id !== id));
  }

  const optionSet = new Set(nameOptions.map((name) => name.toLowerCase()));

  return (
    <CrmSection
      title={title}
      icon={icon}
      actions={
        <Button type="button" variant="outline" size="xs" className="cursor-pointer" onClick={addRow}>
          <Plus className="size-3" aria-hidden />
          Add row
        </Button>
      }
    >
      <div className="erp-scroll overflow-x-auto">
        <table className="w-full min-w-[720px] border-collapse text-left text-sm">
          <thead>
            <tr className={CRM_TABLE_HEAD_ROW}>
              <th className={CRM_TABLE_HEAD_CELL}>
                {nameLabel}
                {nameRequired ? " *" : ""}
              </th>
              <th className={CRM_TABLE_HEAD_CELL}>Contact Person</th>
              <th className={CRM_TABLE_HEAD_CELL}>Contact Number</th>
              <th className={CRM_TABLE_HEAD_CELL}>Contact Email</th>
              <th className={cn(CRM_TABLE_HEAD_CELL, "w-12 text-center")}>
                <span className="sr-only">Remove</span>
              </th>
            </tr>
          </thead>
          <tbody>
            {displayRows.map((row) => {
              const nameInList = optionSet.has(row.name.trim().toLowerCase());
              const selectValue =
                !row.name.trim()
                  ? ""
                  : nameInList
                    ? nameOptions.find((option) => option.toLowerCase() === row.name.trim().toLowerCase()) ??
                    row.name
                    : allowCustomName
                      ? "__custom__"
                      : row.name;

              return (
                <tr key={row.id} className="border-b border-border/60">
                  <td className="min-w-[200px] px-3 py-2 align-top">
                    <div className="space-y-1.5">
                      <FinanceSelect
                        value={selectValue === "__custom__" ? "__custom__" : selectValue}
                        onChange={(event) => {
                          const next = event.target.value;
                          if (next === "__custom__") {
                            updateRow(row.id, { name: nameInList ? "" : row.name });
                            return;
                          }
                          updateRow(row.id, { name: next });
                        }}
                        aria-label={nameLabel}
                      >
                        <option value="">Select…</option>
                        {nameOptions.map((option) => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                        {allowCustomName ? <option value="__custom__">Custom name…</option> : null}
                      </FinanceSelect>
                      {allowCustomName && selectValue === "__custom__" ? (
                        <Input
                          value={nameInList ? "" : row.name}
                          placeholder="Enter distributor name"
                          onChange={(event) => updateRow(row.id, { name: event.target.value })}
                        />
                      ) : null}
                    </div>
                  </td>
                  <td className="min-w-[160px] px-3 py-2 align-top">
                    <Input
                      value={row.contact_person}
                      onChange={(event) => updateRow(row.id, { contact_person: event.target.value })}
                      disabled={!row.name.trim()}
                    />
                  </td>
                  <td className="min-w-[140px] px-3 py-2 align-top">
                    <Input
                      value={row.contact_number}
                      inputMode="tel"
                      autoComplete="tel"
                      onChange={(event) => updateRow(row.id, { contact_number: event.target.value })}
                      disabled={!row.name.trim()}
                    />
                  </td>
                  <td className="min-w-[180px] px-3 py-2 align-top">
                    <Input
                      type="email"
                      value={row.contact_email}
                      autoComplete="email"
                      onChange={(event) => updateRow(row.id, { contact_email: event.target.value })}
                      disabled={!row.name.trim()}
                    />
                  </td>
                  <td className="px-2 py-2 align-top text-center">
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon-xs"
                      className="cursor-pointer text-muted-foreground hover:text-destructive"
                      aria-label={`Remove ${nameLabel.toLowerCase()} row`}
                      onClick={() => removeRow(row.id)}
                    >
                      <Trash2 className="size-3.5" aria-hidden />
                    </Button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </CrmSection>
  );
}
