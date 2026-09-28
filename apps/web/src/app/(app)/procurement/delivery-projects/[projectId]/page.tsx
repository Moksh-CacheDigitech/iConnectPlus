import { DeliveryProjectDetailPage } from "@/components/procurement/delivery-project-detail-page";

interface PageProps {
  params: Promise<{ projectId: string }>;
}

export default async function ProcurementDeliveryProjectDetailPage({ params }: PageProps) {
  const { projectId } = await params;
  return <DeliveryProjectDetailPage projectId={projectId} />;
}
