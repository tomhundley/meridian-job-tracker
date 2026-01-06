import { redirect } from "next/navigation";

export default function Home() {
  // Redirect to dashboard or login
  const localDevBypass =
    process.env.NODE_ENV !== "production" &&
    process.env.LOCAL_DEV_BYPASS === "true";
  redirect(localDevBypass ? "/dashboard" : "/login");
}
