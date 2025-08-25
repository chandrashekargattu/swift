"use client";

import { useState } from "react";
import { Share2, Facebook, Twitter, Linkedin, Mail, MessageSquare, Send } from "lucide-react";

interface SocialShareProps {
  title: string;
  description?: string;
  url?: string;
  shareLinks?: {
    facebook?: string;
    twitter?: string;
    linkedin?: string;
    whatsapp?: string;
    telegram?: string;
    email?: string;
  };
}

export default function SocialShare({
  title,
  description,
  url,
  shareLinks,
}: SocialShareProps) {
  const [showShare, setShowShare] = useState(false);
  const [copied, setCopied] = useState(false);

  const defaultUrl = typeof window !== "undefined" ? window.location.href : "";
  const shareUrl = url || defaultUrl;

  // Generate default share links if not provided
  const links = shareLinks || {
    facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`,
    twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(shareUrl)}`,
    linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`,
    whatsapp: `https://wa.me/?text=${encodeURIComponent(title + " " + shareUrl)}`,
    telegram: `https://t.me/share/url?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(title)}`,
    email: `mailto:?subject=${encodeURIComponent(title)}&body=${encodeURIComponent((description || title) + " " + shareUrl)}`,
  };

  const handleShare = (platform: keyof typeof links) => {
    const link = links[platform];
    if (link) {
      window.open(link, "_blank", "width=600,height=400");
    }
  };

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(shareUrl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setShowShare(!showShare)}
        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
      >
        <Share2 className="w-4 h-4" />
        Share
      </button>

      {showShare && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setShowShare(false)}
          />
          <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-xl border border-gray-200 z-50">
            <div className="p-4">
              <h3 className="text-sm font-semibold text-gray-900 mb-3">
                Share this
              </h3>
              
              <div className="grid grid-cols-3 gap-3">
                <button
                  onClick={() => handleShare("facebook")}
                  className="flex flex-col items-center gap-1 p-2 hover:bg-gray-50 rounded-lg transition-colors"
                >
                  <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                    <Facebook className="w-5 h-5 text-white" />
                  </div>
                  <span className="text-xs text-gray-600">Facebook</span>
                </button>

                <button
                  onClick={() => handleShare("twitter")}
                  className="flex flex-col items-center gap-1 p-2 hover:bg-gray-50 rounded-lg transition-colors"
                >
                  <div className="w-10 h-10 bg-black rounded-lg flex items-center justify-center">
                    <Twitter className="w-5 h-5 text-white" />
                  </div>
                  <span className="text-xs text-gray-600">Twitter</span>
                </button>

                <button
                  onClick={() => handleShare("linkedin")}
                  className="flex flex-col items-center gap-1 p-2 hover:bg-gray-50 rounded-lg transition-colors"
                >
                  <div className="w-10 h-10 bg-blue-700 rounded-lg flex items-center justify-center">
                    <Linkedin className="w-5 h-5 text-white" />
                  </div>
                  <span className="text-xs text-gray-600">LinkedIn</span>
                </button>

                <button
                  onClick={() => handleShare("whatsapp")}
                  className="flex flex-col items-center gap-1 p-2 hover:bg-gray-50 rounded-lg transition-colors"
                >
                  <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center">
                    <MessageSquare className="w-5 h-5 text-white" />
                  </div>
                  <span className="text-xs text-gray-600">WhatsApp</span>
                </button>

                <button
                  onClick={() => handleShare("telegram")}
                  className="flex flex-col items-center gap-1 p-2 hover:bg-gray-50 rounded-lg transition-colors"
                >
                  <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center">
                    <Send className="w-5 h-5 text-white" />
                  </div>
                  <span className="text-xs text-gray-600">Telegram</span>
                </button>

                <button
                  onClick={() => handleShare("email")}
                  className="flex flex-col items-center gap-1 p-2 hover:bg-gray-50 rounded-lg transition-colors"
                >
                  <div className="w-10 h-10 bg-gray-600 rounded-lg flex items-center justify-center">
                    <Mail className="w-5 h-5 text-white" />
                  </div>
                  <span className="text-xs text-gray-600">Email</span>
                </button>
              </div>

              <div className="mt-4 pt-4 border-t border-gray-200">
                <button
                  onClick={handleCopyLink}
                  className="w-full px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm text-gray-700 transition-colors"
                >
                  {copied ? "✓ Copied!" : "Copy Link"}
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
