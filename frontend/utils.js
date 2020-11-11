export function parseDateTime(datetime) {
  return new Date(Date.parse(datetime.replace(" ", "T")) - 2 * 60 * 60 * 1000);
}

export function datetimeToHour(datetime) {
  return parseDateTime(datetime).toLocaleTimeString().slice(0, 5);
}

export function censorUuid(uuid) {
  return uuid.slice(0, 8) + "-****-****-****-************";
}

export function filterTransfers(actions) {
  const isTransfer = (transfer) => transfer.type === "transfer";
  return actions.filter(isTransfer);
}

export const validateUuid = (string) => {
  const re = new RegExp(
    "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$"
  );
  return re.test(string);
};

export const validateLink = (string) => {
  const re = new RegExp(
    "^krk-meetings://[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$"
  );
  return re.test(string);
};

export const sleep = (ms) => {
  return new Promise((r) => setTimeout(r, ms));
};
