import { redirect } from "next/navigation";

/** Templates UI removed — Email module is compose + delivery only. */
export default function EmailTemplatesRoute() {
  redirect("/email");
}
