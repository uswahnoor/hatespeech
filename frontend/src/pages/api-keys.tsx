import React from "react";
import ApiKeyManager from "@/components/ApiKeyManager";

const ApiKeysPage: React.FC = () => {
  return (
    <div className="max-w-2xl mx-auto py-10">
      <h1 className="text-3xl font-bold mb-6">Manage Your API Keys</h1>
      <ApiKeyManager />
    </div>
  );
};

export default ApiKeysPage;
