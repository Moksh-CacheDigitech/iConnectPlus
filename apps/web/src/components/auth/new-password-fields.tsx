"use client";

import { Check, Circle } from "lucide-react";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

const POLICY_RULES: { label: string; test: (value: string) => boolean }[] = [
  { label: "8+ characters", test: (v) => v.length >= 8 },
  { label: "Upper & lower case", test: (v) => /[a-z]/.test(v) && /[A-Z]/.test(v) },
  { label: "A number", test: (v) => /\d/.test(v) },
  { label: "A symbol", test: (v) => /[^A-Za-z0-9]/.test(v) },
];

/** Mirrors the API password policy (security/password.py). */
export function passwordMeetsPolicy(value: string): boolean {
  return POLICY_RULES.every((rule) => rule.test(value));
}

export function NewPasswordFields({
  password,
  confirm,
  onPasswordChange,
  onConfirmChange,
  disabled,
}: {
  password: string;
  confirm: string;
  onPasswordChange: (value: string) => void;
  onConfirmChange: (value: string) => void;
  disabled?: boolean;
}) {
  const mismatch = confirm.length > 0 && confirm !== password;
  return (
    <>
      <div>
        <Label htmlFor="new-password">New password</Label>
        <Input
          id="new-password"
          type="password"
          autoComplete="new-password"
          required
          value={password}
          disabled={disabled}
          onChange={(e) => onPasswordChange(e.target.value)}
          className="h-10"
          aria-describedby="new-password-rules"
        />
        <ul id="new-password-rules" className="mt-2 grid grid-cols-2 gap-x-3 gap-y-1 text-xs">
          {POLICY_RULES.map((rule) => {
            const ok = rule.test(password);
            return (
              <li
                key={rule.label}
                className={`flex items-center gap-1.5 ${ok ? "text-emerald-700" : "text-muted-foreground"}`}
              >
                {ok ? (
                  <Check className="size-3" aria-hidden />
                ) : (
                  <Circle className="size-2" aria-hidden />
                )}
                {rule.label}
              </li>
            );
          })}
        </ul>
      </div>
      <div>
        <Label htmlFor="confirm-password">Confirm new password</Label>
        <Input
          id="confirm-password"
          type="password"
          autoComplete="new-password"
          required
          value={confirm}
          disabled={disabled}
          onChange={(e) => onConfirmChange(e.target.value)}
          className="h-10"
          aria-invalid={mismatch}
        />
        {mismatch ? (
          <p className="mt-1 text-xs text-destructive">Passwords do not match.</p>
        ) : null}
      </div>
    </>
  );
}
