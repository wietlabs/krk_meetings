const axios = require("axios");

const baseUrl = "http://10.0.0.5:8000";

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

export const createUser = async () => {
  const url = `${baseUrl}/api/v1/users`;
  const response = await axios.post(url);
  const uuid = response.data["uuid"];
  return { uuid: uuid };
};

export const getMeetings = async ({ userUuid }) => {
  const url = `${baseUrl}/api/v1/users/${userUuid}/meetings`;
  const response = await axios.get(url);
  const meetings = response.data["meetings"];
  return meetings;
};

export const getMeeting = async (meetingUuid) => {
  const url = `${baseUrl}/api/v1/meetings/${meetingUuid}`;
  const response = await axios.get(url);
  const meeting = response.data;
  return meeting;
};

export const createMeeting = async ({ userUuid, nickname, name }) => {
  const url = `${baseUrl}/api/v1/meetings`;
  const params = {
    user_uuid: userUuid,
    nickname: nickname,
    name: name,
  };
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

export const joinMeeting = async ({ meetingUuid, userUuid, nickname }) => {
  const url = `${baseUrl}/api/v1/meetings/${meetingUuid}/members`;
  const params = {
    user_uuid: userUuid,
    nickname: nickname,
  };
  await axios.post(url, params);
};
