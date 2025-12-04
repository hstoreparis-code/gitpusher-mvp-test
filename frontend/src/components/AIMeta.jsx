export function AIMeta() {
  return (
    <>
      <link rel="openapi" href="/api/openapi.yaml" />
      <meta name="ai:actions" content="/ai/ai-actions.json" />
      <meta name="ai:indexers" content="/ai/indexers/ai-indexers.json" />
      <meta name="ai:indexers:extended" content="/ai/indexers/ai-80-indexers.json" />
      <meta name="ai:knowledge" content="/ai/knowledge/intent-map.json" />
    </>
  );
}

export default AIMeta;
