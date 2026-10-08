"use client";

import type { ReactNode } from "react";
import { Suspense } from "react";

import { ProjectsMemberRouteGuard } from "@/components/projects/projects-member-route-guard";
import { ProjectStageFollowUpInbox } from "@/components/projects/project-stage-follow-up-inbox";

export default function ProjectsLayout({ children }: { children: ReactNode }) {
  return (
    <Suspense fallback={<div className="min-w-0 max-w-full overflow-x-clip">{children}</div>}>
      <div className="min-w-0 max-w-full overflow-x-clip">
        <ProjectStageFollowUpInbox />
        <ProjectsMemberRouteGuard>{children}</ProjectsMemberRouteGuard>
      </div>
    </Suspense>
  );
}
