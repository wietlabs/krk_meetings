import * as React from "react";
import { Text, View } from "react-native";
import { IconButton } from "react-native-paper";
import { filterTransfers, parseDateTime } from "../../../utils";

const colors = ["skyblue", "lime", "gold", "darkorange", "tomato"];

const getColor = (n) => colors[Math.min(n, colors.length - 1)];

export default function ConnectionResultsPlotScreen({ navigation, route }) {
  const connections = route.params.connections;

  const start_datetime = parseDateTime("2020-05-24 20:00:00");

  const handleShow = (connection) => {
    navigation.navigate("ConnectionDetails", { connection: connection });
  };

  const calculateX = (minutes) => 80 + 10 * minutes;
  const calculateY = (minutes) => 60 + 6 * minutes;

  const horizontalLine = (y, label) => {
    return (
      <View
        style={{
          position: "absolute",
          top: y,
          left: 0,
          right: 0,
          borderTopColor: "lightgray",
          borderTopWidth: 1,
          paddingLeft: 8,
        }}
      >
        <IconButton
          icon="timer"
          size={20}
          color="lightgray"
          style={{ margin: 0 }}
        />
        <Text style={{ color: "lightgray" }}>{label}</Text>
      </View>
    );
  };

  const verticalLine = (x, label) => {
    return (
      <View
        style={{
          position: "absolute",
          left: x,
          top: 0,
          bottom: 0,
          borderLeftColor: "lightgray",
          borderLeftWidth: 1,
          paddingTop: 4,
          paddingLeft: 4,
        }}
      >
        <IconButton
          icon="walk"
          size={20}
          color="lightgray"
          style={{ margin: 0 }}
        />
        <Text style={{ color: "lightgray" }}>{label}</Text>
      </View>
    );
  };

  return (
    <>
      {verticalLine(calculateX(0), "0 m")}
      {verticalLine(calculateX(10), "300 m")}
      {verticalLine(calculateX(20), "600 m")}
      {horizontalLine(calculateY(0), "0 min")}
      {horizontalLine(calculateY(15), "15 min")}
      {horizontalLine(calculateY(30), "30 min")}
      {horizontalLine(calculateY(45), "45 min")}
      {horizontalLine(calculateY(60), "60 min")}
      {horizontalLine(calculateY(75), "75 min")}
      <View>
        {connections.map((connection, i) => {
          const actions = connection.transfers;
          const transfers = filterTransfers(actions);

          const first_transfer = transfers[0];
          const last_transfer = transfers[transfers.length - 1];

          // const start_datetime = parseDateTime(first_transfer.start_datetime);
          const end_datetime = parseDateTime(last_transfer.end_datetime);

          const duration_ms = end_datetime - start_datetime;
          const duration_minutes = duration_ms / 1000 / 60;

          const walking_minutes = actions
            .filter((action) => action.type === "walking")
            .map((walking) => walking.duration_in_minutes)
            .reduce((a, b) => a + b, 0);

          const number_of_transfers = transfers.length;
          const color = getColor(number_of_transfers);

          const x = calculateX(walking_minutes);
          const y = calculateY(duration_minutes);

          return (
            <Text
              key={i}
              onPress={() => handleShow(connection)}
              style={{
                left: x - 12,
                top: y - 12,
                zIndex: 9999 - x,
                width: 24,
                height: 24,
                position: "absolute",
                backgroundColor: color,
                borderRadius: 12,
                textAlign: "center",
                textAlignVertical: "center",
                fontWeight: "bold",
                color: "white",
              }}
            >
              {number_of_transfers}
            </Text>
          );
        })}
      </View>
    </>
  );
}
