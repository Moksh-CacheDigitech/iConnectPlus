import { QuoteFormPage } from "@/components/crm/sales/quote-form-page";

interface PageProps {
  searchParams: Promise<{ opportunityId?: string; opportunity_id?: string }>;
}

export default async function CrmQuoteNewRoute({ searchParams }: PageProps) {
  const params = await searchParams;
  const opportunityId = params.opportunityId ?? params.opportunity_id;
  return <QuoteFormPage opportunityId={opportunityId} />;
}
