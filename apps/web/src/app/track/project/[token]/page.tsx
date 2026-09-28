import type { Metadata } from "next";

import { ProjectTrackingPortal } from "@/components/procurement/project-tracking-portal";

export const metadata: Metadata = {
  title: "Delivery tracker",
  description: "Site-by-site delivery status for your rollout.",
  robots: { index: false, follow: false },
};

interface PageProps {
  params: Promise<{ token: string }>;
}

export default async function ProjectTrackingPage({ params }: PageProps) {
  const { token } = await params;
  return <ProjectTrackingPortal token={token} />;
}
