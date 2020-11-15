import * as Linking from "expo-linking";

export function createUserLink(uuid) {
  return Linking.makeUrl("user", { uuid });
}

export function createMeetingLink(uuid) {
  return Linking.makeUrl("meeting", { uuid });
}

const uuidv4Pattern =
  "[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}";

const userLinkRe = new RegExp("/user\\?uuid=" + uuidv4Pattern + "$");

const meetingLinkRe = new RegExp("/meeting\\?uuid=" + uuidv4Pattern + "$");

export function validateUserLink(link) {
  console.log(link);
  return userLinkRe.test(link);
}

export function validateMeetingLink(link) {
  return meetingLinkRe.test(link);
}

export function getUuidFromLink(link) {
  const { path, queryParams } = Linking.parse(link);
  return queryParams.uuid;
}
