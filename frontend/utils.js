export function parseDateTime(datetime) {
  return new Date(Date.parse(datetime.replace(" ", "T")));
}

export function datetimeToHour(datetime) {
  return parseDateTime(datetime).toLocaleTimeString().slice(0, 5);
}

export const makeDateTime = (date, time) => {
  return new Date(
    date.getYear() + 1900,
    date.getMonth(),
    date.getDate(),
    time.getHours(),
    time.getMinutes(),
    time.getSeconds()
  );
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

export const createRandomNickname = () => {
  return "Guest#" + Math.floor(Math.random() * 10000).toString();
};

export const getMeetingOwnerNickname = (meeting) => {
  return meeting.members.filter((member) => member.is_owner)[0].nickname;
};
