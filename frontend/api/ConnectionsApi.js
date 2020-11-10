const axios = require("axios");

const baseUrl = "http://10.0.0.5:5000";

export const getStops = async () => {
  const url = `${baseUrl}/stops`;
  const response = await axios.get(url);
  const stops = response.data.stops;
  return stops;
};

export const findConnections = async (
  { startDateTime, startStopName, endStopName },
  interval = 500,
  retries = 10
) => {
  const url = `${baseUrl}/connection`;
  const params = {
    start_datetime: "2020-11-10 16:00:00", // TODO: handle
    start_stop_name: startStopName,
    end_stop_name: endStopName,
  };
  const response = await axios.post(url, params);
  const queryId = response.data;

  for (let i = 0; i < retries; ++i) {
    const connections = await getResults(queryId);
    if (connections !== null) return connections;
    await new Promise((r) => setTimeout(r, interval));
  }
  throw new Error("Reached max retries");
};

const getResults = async (queryId) => {
  const url = `${baseUrl}/result/${queryId}`;
  const response = await axios.get(url);
  const ready = response.data.is_done;
  if (!ready) return null;
  const connections = response.data.connections;
  return connections;
};
