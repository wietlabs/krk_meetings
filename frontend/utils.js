export function parseDateTime(datetime) {
  return new Date(Date.parse(datetime.replace(" ", "T")));
}

export function formatDateTime(datetime) {
  return datetime.toISOString().slice(0, 19).replace("T", " ");
}

export function formatDateTimeForHumans(datetime) {
  const date = formatDate(datetime);
  const time = formatTime(datetime);
  return `${date} r., godz. ${time}`;
}

export function formatDate(date) {
  // return date.toISOString().slice(0, 10);
  return [
    date.getDate().toString().padStart(2, "0"),
    (date.getMonth() + 1).toString().padStart(2, "0"),
    date.getFullYear(),
  ].join(".");
}

export function formatTime(time) {
  return time.toISOString().slice(11, 16);
}

export const makeDateTime = (date, time) => {
  const dt = new Date(
    date.getFullYear(),
    date.getMonth(),
    date.getDate(),
    time.getHours(),
    time.getMinutes()
  );
  return dt;
  // return new Date(dt.getTime() - dt.getTimezoneOffset() * 60 * 1000);
};

export function censorUuid(uuid) {
  return uuid.slice(0, 8) + "-****-****-****-************";
}

export const validateUuid = (string) => {
  const re = new RegExp(
    "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$"
  );
  return re.test(string);
};

export function filterTransfers(actions) {
  const isTransfer = (transfer) => transfer.type === "transfer";
  return actions.filter(isTransfer);
}

export const sleep = (ms) => {
  return new Promise((r) => setTimeout(r, ms));
};

export const generateRandomNickname = () => {
  const digits = (Math.floor(Math.random() * 10000) + 10000)
    .toString()
    .substring(1);
  return "Guest#" + digits;
};

export const getMeetingMembersStopNames = (meeting) => {
  return meeting.members.map((member) => member.stop_name).filter((x) => x);
};

export const getStopsByNames = (stopNames, stops) => {
  const findStopByName = (stopName) =>
    stops.find((stop) => stop.name === stopName);

  return stopNames.map(findStopByName);
};
