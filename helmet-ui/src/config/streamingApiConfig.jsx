function trimTrailingSlash(url) {
  if (!url) return "";
  return url.replace(/\/+$/, "");
}

function httpOriginToWsOrigin(httpBase) {
  if (!httpBase) return "";

  if (httpBase.startsWith("https://")) {
    return `wss://${httpBase.slice("https://".length)}`;
  }

  if (httpBase.startsWith("http://")) {
    return `ws://${httpBase.slice("http://".length)}`;
  }

  return httpBase;
}


export const HELMET_MONITORING_API_BASE = trimTrailingSlash(
  import.meta.env.VITE_HELMET_MONITORING_SERVER_URL
);
export const OTP_SERVER_URL = trimTrailingSlash(
  import.meta.env.OTP_SERVER_URL
);

export const HELMET_MONITORING_WS_BASE =
  httpOriginToWsOrigin(HELMET_MONITORING_API_BASE);

export const ATTENDANCE_API_BASE = trimTrailingSlash(
  import.meta.env.VITE_ATTENDANCE_SERVER_URL
);

export const ATTENDANCE_WS_BASE =
  httpOriginToWsOrigin(ATTENDANCE_API_BASE);