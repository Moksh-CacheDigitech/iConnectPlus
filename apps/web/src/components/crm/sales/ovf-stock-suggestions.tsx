"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Boxes } from "lucide-react";

import { CrmSection } from "@/components/crm/crm-ui";
import { suggestInventory, type InventoryUnit } from "@/services/crm-deal-controls-service";
import { formatInr, listOvfLines, type Ovf } from "@/services/sales-crm-service";

type Match = { product: string; units: InventoryUnit[] };

/**
 * Before SCM orders fresh stock, show units already in the warehouse that
 * match this OVF - at today's value (cost plus carrying cost).
 */
export function OvfStockSuggestions({ ovf }: { ovf: Ovf }) {
  const relevant = !ovf.deal_won && !ovf.closed_at;
  const [matches, setMatches] = useState<Match[]>([]);

  useEffect(() => {
    if (!relevant) return;
    let cancelled = false;
    void (async () => {
      const lines = await listOvfLines(ovf.id).catch(() => []);
      const products = [...new Set(lines.filter((l) => l.side === "customer_po").map((l) => l.product_name.trim()))]
        .filter((name) => name.length >= 3)
        .slice(0, 8);
      const found: Match[] = [];
      for (const product of products) {
        const units = await suggestInventory(product).catch(() => []);
        if (units.length) found.push({ product, units });
      }
      if (!cancelled) setMatches(found);
    })();
    return () => {
      cancelled = true;
    };
  }, [ovf.id, relevant]);

  if (!relevant || matches.length === 0) return null;

  return (
    <CrmSection title="Matching Stock Already On Hand" icon={Boxes}>
      <p className="mb-2 text-xs text-muted-foreground">
        Use existing stock before buying fresh. Today&apos;s value includes 1% a month carrying cost since it arrived.
      </p>
      <ul className="space-y-1.5 text-[13px]">
        {matches.map(({ product, units }) => {
          const open = units.filter((u) => u.status === "open_for_sale").length;
          const oldest = Math.max(...units.map((u) => u.age_days));
          const value = units.reduce((sum, u) => sum + Number(u.current_value), 0);
          return (
            <li key={product} className="flex flex-wrap items-center justify-between gap-2 rounded-lg border border-border/70 px-3 py-2">
              <span>
                <span className="font-medium">{product}</span>: {units.length} unit(s) on hand, {open} open for sale, oldest{" "}
                {oldest} days
              </span>
              <span className="tabular-nums text-muted-foreground">Today&apos;s value {formatInr(value)}</span>
            </li>
          );
        })}
      </ul>
      <Link
        href="/crm/inventory-aging"
        className="mt-2 inline-block cursor-pointer text-xs font-medium text-primary underline underline-offset-2"
      >
        Open stock &amp; request units
      </Link>
    </CrmSection>
  );
}
