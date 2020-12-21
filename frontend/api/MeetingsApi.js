import { formatDateTime } from "../utils";

const axios = require("axios");

const baseUrl = "http://10.0.0.20:8000";

export const createUser = async () => {
  const url = `${baseUrl}/api/v1/users`;
  const response = await axios.post(url);
  const uuid = response.data["uuid"];
  return { uuid };
};

export const checkIfUserExists = async (uuid) => {
  const url = `${baseUrl}/api/v1/users/${uuid}`;
  try {
    await axios.get(url);
    return true;
  } catch (e) {
    if (e.response.status === 404) return false;
    throw e;
  }
};

export const getUserMeetings = async (userUuid) => {
  const url = `${baseUrl}/api/v1/users/${userUuid}/meetings`;
  const response = await axios.get(url);
  const meetings = response.data["meetings"];
  return meetings;
};

export const createMeeting = async ({ userUuid, nickname, name }) => {
  const url = `${baseUrl}/api/v1/meetings`;
  const params = { owner_uuid: userUuid, nickname, name };
  const response = await axios.post(url, params);
  const uuid = response.data["uuid"];
  return { uuid };
};

export const checkIfMeetingExists = async (meetingUuid) => {
  const url = `${baseUrl}/api/v1/meetings/${meetingUuid}`;
  try {
    await axios.get(url);
    return true;
  } catch (e) {
    if (e.response.status === 404) return false;
    throw e;
  }
};

export const getMeetingJoinInfo = async (meetingUuid) => {
  const url = `${baseUrl}/api/v1/meetings/${meetingUuid}`;
  const response = await axios.get(url);
  const meeting = response.data;
  return meeting;
};

export const updateMeetingDateTime = async ({
  meetingUuid,
  userUuid,
  datetime,
}) => {
  const url = `${baseUrl}/api/v1/meetings/${meetingUuid}`;
  const params = { owner_uuid: userUuid, datetime: formatDateTime(datetime) };
  await axios.patch(url, params);
};

export const updateMeetingStopName = async ({
  meetingUuid,
  userUuid,
  stopName,
}) => {
  const url = `${baseUrl}/api/v1/meetings/${meetingUuid}`;
  const params = { owner_uuid: userUuid, stop_name: stopName };
  await axios.patch(url, params);
};

export const joinMeeting = async ({ meetingUuid, userUuid, nickname }) => {
  const url = `${baseUrl}/api/v1/memberships/${meetingUuid}/${userUuid}`;
  const params = { nickname };
  await axios.put(url, params);
};

export const getMembershipDetails = async ({ meetingUuid, userUuid }) => {
  const url = `${baseUrl}/api/v1/memberships/${meetingUuid}/${userUuid}`;
  const response = await axios.get(url);
  const meeting = response.data;
  return meeting;
};

export const updateMembershipStopName = async ({
  meetingUuid,
  userUuid,
  stopName,
}) => {
  const url = `${baseUrl}/api/v1/memberships/${meetingUuid}/${userUuid}`;
  const params = { stop_name: stopName };
  await axios.patch(url, params);
};

export const leaveMeeting = async ({ meetingUuid, userUuid }) => {
  const url = `${baseUrl}/api/v1/memberships/${meetingUuid}/${userUuid}`;
  await axios.delete(url);
};

export const deleteMeeting = async ({ meetingUuid, userUuid }) => {
  const url = `${baseUrl}/api/v1/meetings/${meetingUuid}`;
  const params = { owner_uuid: userUuid };
  await axios.delete(url, { data: params });
};
