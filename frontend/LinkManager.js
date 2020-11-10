export function createUserLink(uuid) {
  return `krk-meetings://user/${uuid}`;
}

export function createMeetingLink(uuid) {
  return `krk-meetings://meeting/${uuid}`;
}

const userLinkRe = new RegExp(
  "^krk-meetings://user/[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$"
);

const meetingLinkRe = new RegExp(
  "^krk-meetings://meeting/[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$"
);

export function validateUserLink(link) {
  return userLinkRe.test(link);
}

export function validateMeetingLink(link) {
  return meetingLinkRe.test(link);
}

export function parseUserLink(link) {
  return link.slice("krk-meetings://user/".length);
}

export function parseMeetingLink(link) {
  return link.slice("krk-meetings://meeting/".length);
}
