/**
 * Locked platform split (Architecture Lock + FRD-01/02/03):
 * Foundation = access & engines; Organization = structure; Master Data = shared masters.
 */

export type PlatformPillarKey = "foundation" | "organization" | "master-data";

export type PlatformPillar = {
  key: PlatformPillarKey;
  title: string;
  /** One-line product rule. */
  rule: string;
  href: string;
};

export const PLATFORM_PILLARS: readonly PlatformPillar[] = [
  {
    key: "foundation",
    title: "Foundation",
    rule: "Who can do what + how approvals, notifications, and audit work.",
    href: "/foundation",
  },
  {
    key: "organization",
    title: "Organization",
    rule: "Where the company structure is (companies, branches, departments).",
    href: "/organization",
  },
  {
    key: "master-data",
    title: "Master Data",
    rule: "Shared business masters used across every module.",
    href: "/master-data",
  },
] as const;

export function platformPillarForModuleKey(moduleKey: string): PlatformPillarKey | null {
  if (moduleKey === "foundation" || moduleKey === "organization" || moduleKey === "master-data") {
    return moduleKey;
  }
  return null;
}
