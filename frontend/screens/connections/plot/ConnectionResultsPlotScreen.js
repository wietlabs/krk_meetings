import * as React from "react";
import { Text, View, ScrollView } from "react-native";
import { IconButton } from "react-native-paper";
import { filterTransfers, parseDateTime } from "../../../utils";

const bubbleSize = 26;

const colors = [
  "dodgerblue",
  "lime",
  "gold",
  "darkorange",
  "tomato",
  "crimson",
];

const getColor = (n) => colors[Math.min(n, colors.length - 1)];

export default function ConnectionResultsPlotScreen({ navigation, route }) {
  const start_datetime = new Date(route.params.startDateTime);
  const connections = route.params.connections;

  const handleShow = (connection) => {
    navigation.navigate("ConnectionDetails", { connection: connection });
  };

  const calculateX = (minutes) => 100 + 18 * minutes;
  const calculateY = (minutes) => 60 + 8 * minutes;

  const horizontalLine = (y, label) => {
    return (
      <View
        key={"horizontal-" + y}
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
        {label && (
          <>
            <IconButton
              icon="timer"
              size={20}
              color="lightgray"
              style={{ margin: 0 }}
            />
            <Text style={{ color: "lightgray" }}>{label}</Text>
          </>
        )}
      </View>
    );
  };

  const verticalLine = (x, label) => {
    return (
      <View
        key={"vertical-" + x}
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

  let horizontalLines = [];
  for (let i = 0; i <= 120; i += 15) {
    horizontalLines.push(horizontalLine(calculateY(i), i + " min"));
  }

  let verticalLines = [];
  for (let i = 0; i <= 30; i += 5) {
    verticalLines.push(verticalLine(calculateX(i), i + " min"));
  }

  return (
    <>
      {verticalLines}
      <ScrollView>
        {horizontalLines}
        <View style={{ height: 1100 }}>
          {connections.map((connection, i) => {
            const actions = connection.actions;
            const transfers = filterTransfers(actions);

            const last_transfer = transfers[transfers.length - 1];

            const end_datetime = parseDateTime(last_transfer.end_datetime);

            const duration_ms = end_datetime - start_datetime;
            const duration_minutes = duration_ms / 1000 / 60;

            const walking_minutes = actions
              .filter((action) => action.type === "walking")
              .map((walking) => walking.duration_in_minutes)
              .reduce((a, b) => a + b, 0);

            const number_of_transfers = connection.transfers_count;
            const color = getColor(number_of_transfers);

            const x = calculateX(walking_minutes);
            const y = calculateY(duration_minutes);

            const zIndex = 9999 - number_of_transfers * 100 - duration_minutes;

            return (
              <Text
                key={i}
                onPress={() => handleShow(connection)}
                style={{
                  left: x - bubbleSize / 2,
                  top: y - bubbleSize / 2,
                  zIndex: zIndex,
                  width: bubbleSize,
                  height: bubbleSize,
                  position: "absolute",
                  backgroundColor: color,
                  borderRadius: bubbleSize / 2,
                  textAlign: "center",
                  textAlignVertical: "center",
                  fontWeight: "bold",
                  fontSize: bubbleSize * 0.6,
                  color: "white",
                }}
              >
                {number_of_transfers}
              </Text>
            );
          })}
        </View>
      </ScrollView>
    </>
  );
}
