import "dotenv/config";

export default ({ config }) => {
  return {
    ...config,
    extra: {
      backendApiBaseUrl:
        process.env.BACKEND_API_BASE_URL || "http://10.0.0.6:5000",
      meetingsApiBaseUrl:
        process.env.MEETINGS_API_BASE_URL || "http://10.0.0.6:8000",
    },
  };
};
