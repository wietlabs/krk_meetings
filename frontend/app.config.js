import "dotenv/config";

export default {
  name: "Krk Meetings",
  slug: "krk_meetings",
  scheme: "krkmeet",
  version: "1.0.0",
  orientation: "portrait",
  icon: "./assets/icon.png",
  splash: {
    image: "./assets/splash.png",
    resizeMode: "contain",
    backgroundColor: "#ffffff",
  },
  updates: {
    fallbackToCacheTimeout: 0,
  },
  assetBundlePatterns: ["**/*"],
  ios: {
    supportsTablet: true,
  },
  web: {
    favicon: "./assets/favicon.png",
  },
  extra: {
    backendApiBaseUrl:
      process.env.BACKEND_API_BASE_URL || "http://10.0.0.6:5000",
    meetingsApiBaseUrl:
      process.env.MEETINGS_API_BASE_URL || "http://10.0.0.6:8000",
  },
};
