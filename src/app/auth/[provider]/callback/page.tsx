"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { apiClient } from "@/lib/api/client";

export default function OAuthCallback({
  params,
}: {
  params: { provider: string };
}) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { setUser } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const handleCallback = async () => {
      try {
        const code = searchParams.get("code");
        const state = searchParams.get("state");
        const codeVerifier = sessionStorage.getItem("code_verifier");

        if (!code || !state) {
          throw new Error("Missing authorization code or state");
        }

        // Call backend OAuth callback endpoint
        const response = await apiClient.get(
          `/oauth/auth/${params.provider}/callback`,
          {
            params: {
              code,
              state,
              ...(codeVerifier && { code_verifier: codeVerifier }),
            },
          }
        );

        if (response.data && response.data.access_token) {
          // Store token and user info
          localStorage.setItem("accessToken", response.data.access_token);
          setUser(response.data.user);

          // Clear session storage
          sessionStorage.removeItem("code_verifier");
          sessionStorage.removeItem("oauth_state");

          // Redirect to dashboard or home
          router.push("/");
        }
      } catch (err: any) {
        console.error("OAuth callback error:", err);
        setError(err.message || "Authentication failed");
      } finally {
        setLoading(false);
      }
    };

    handleCallback();
  }, [params.provider, searchParams, router, setUser]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">
            Completing {params.provider} authentication...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md">
          <div className="text-red-600 text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Authentication Failed
          </h1>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => router.push("/signin")}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Back to Sign In
          </button>
        </div>
      </div>
    );
  }

  return null;
}
