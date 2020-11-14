import * as React from "react";
import { Text, View, ScrollView } from "react-native";
import { filterTransfers, parseDateTime } from "../../../utils";
import GridLine from "./GridLine";

const bubbleSize = 26;

const colors = [
  "dodgerblue",
  "lime",
  "gold",
  "darkorange",
  "tomato",
  "crimson",
];

const calculateWalkingMinutes = (connection) =>
  connection.actions
    .filter((action) => action.type === "walking")
    .map((walking) => walking.duration_in_minutes)
    .reduce((a, b) => a + b, 0);

const getColor = (n) => colors[Math.min(n, colors.length - 1)];

const calculateX = (minutes) => 100 + 18 * minutes;
const calculateY = (minutes) => 60 + 8 * minutes;
const calculateZ = (numberOfTransfers, durationMinutes) => {
  return 9999 - numberOfTransfers * 100 - durationMinutes;
};

export default function ConnectionResultsPlotScreen({ navigation, route }) {
  const startDateTime = new Date(route.params.startDateTime);
  const connections = route.params.connections;

  const handleShow = (connection) => {
    navigation.navigate("ConnectionDetails", { connection: connection });
  };

  const calculateDurationMinutes = React.useCallback(
    (connection) => {
      const actions = connection.actions;
      const transfers = filterTransfers(actions);
      const lastTransfer = transfers[transfers.length - 1];
      const endDateTime = parseDateTime(lastTransfer.end_datetime);
      const durationMillis = endDateTime - startDateTime;
      const durationMinutes = durationMillis / 1000 / 60;
      return durationMinutes;
    },
    [startDateTime]
  );

  const lastMinutes = React.useMemo(() => {
    const maxDurationMinutes = Math.max(
      ...connections.map(calculateDurationMinutes)
    );
    return Math.ceil(maxDurationMinutes / 15) * 15 + 12;
  }, [startDateTime, connections]);

  const height = React.useMemo(() => calculateY(lastMinutes), [lastMinutes]);

  let horizontalLines = [];
  for (let minutes = 0; minutes <= lastMinutes; minutes += 15) {
    horizontalLines.push(
      <GridLine
        orientation="horizontal"
        position={calculateY(minutes)}
        icon="clock-outline"
        label={minutes + " min"}
      />
    );
  }

  let verticalLines = [];
  for (let minutes = 0; minutes <= 30; minutes += 5) {
    verticalLines.push(
      <GridLine
        orientation="vertical"
        position={calculateX(minutes)}
        icon="walk"
        label={minutes + " min"}
      />
    );
  }

  return (
    <>
      {verticalLines}
      <ScrollView>
        {horizontalLines}
        <View style={{ height: height }}>
          {connections.map((connection, i) => {
            const durationMinutes = calculateDurationMinutes(connection);
            const walkingMinutes = calculateWalkingMinutes(connection);
            const numberOfTransfers = connection.transfers_count;
            const color = getColor(numberOfTransfers);
            const x = calculateX(walkingMinutes);
            const y = calculateY(durationMinutes);
            const zIndex = calculateZ(numberOfTransfers, durationMinutes);

            return (
              <Text
                key={i}
                onPress={() => handleShow(connection)}
                style={{
                  position: "absolute",
                  left: x - bubbleSize / 2,
                  top: y - bubbleSize / 2,
                  zIndex: zIndex,
                  width: bubbleSize,
                  height: bubbleSize,
                  backgroundColor: color,
                  borderRadius: bubbleSize / 2,
                  fontWeight: "bold",
                  fontSize: bubbleSize * 0.6,
                  textAlign: "center",
                  textAlignVertical: "center",
                  color: "white",
                }}
              >
                {numberOfTransfers}
              </Text>
            );
          })}
        </View>
      </ScrollView>
    </>
  );
}
