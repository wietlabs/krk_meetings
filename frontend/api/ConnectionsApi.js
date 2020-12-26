import { formatDateTime, sleep } from "../utils";

import Constants from "expo-constants";

const axios = require("axios");

const baseUrl = Constants.manifest.extra.backendApiBaseUrl;

export const getStops = async () => {
  const url = `${baseUrl}/stops`;
  const response = await axios.get(url);
  const stops = response.data.stops;
  return stops;
};

export const findConnections = async (
  { startDateTime, startStopName, endStopName },
  first_interval = 500,
  next_interval = 500,
  retries = 20
) => {
  const url = `${baseUrl}/connection`;
  const params = {
    start_datetime: formatDateTime(startDateTime),
    start_stop_name: startStopName,
    end_stop_name: endStopName,
  };
  const response = await axios.post(url, params);
  const queryId = response.data.query_id;

  await sleep(first_interval);

  for (let i = 0; i < retries; ++i) {
    const result = await getResults(queryId);
    if (result !== null) return result.connections;
    await sleep(next_interval);
  }
  throw new Error("Reached max retries");
};

export const findMeetingPoints = async (
  { startStopNames, norm },
  first_interval = 500,
  next_interval = 500,
  retries = 20
) => {
  const url = `${baseUrl}/meeting`;
  const params = { start_stop_names: startStopNames, norm };
  const response = await axios.post(url, params);
  const queryId = response.data.query_id;

  await sleep(first_interval);

  for (let i = 0; i < retries; ++i) {
    const result = await getResults(queryId);
    if (result !== null) return result.meeting_points;
    await sleep(next_interval);
  }
  throw new Error("Reached max retries");
};

export const findOptimalSequence = async (
  { startStopName, stopsToVisit, endStopName },
  first_interval = 500,
  next_interval = 500,
  retries = 20
) => {
  const url = `${baseUrl}/sequence`;
  const params = {
    start_stop_name: startStopName,
    stops_to_visit: stopsToVisit,
    end_stop_name: endStopName,
  };
  const response = await axios.post(url, params);
  const queryId = response.data.query_id;

  await sleep(first_interval);

  for (let i = 0; i < retries; ++i) {
    const result = await getResults(queryId);
    if (result !== null) return result.best_sequence;
    await sleep(next_interval);
  }
  throw new Error("Reached max retries");
};

const getResults = async (queryId) => {
  const url = `${baseUrl}/result/${queryId}`;
  const response = await axios.get(url);
  const ready = response.data.is_done;
  if (!ready) return null;
  const result = response.data;
  return result;
};
