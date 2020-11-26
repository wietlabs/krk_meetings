import * as React from "react";
import { Text, View, ScrollView } from "react-native";
import { filterTransfers, parseDateTime } from "../../../utils";
import GridLine from "./GridLine";

const bubbleSize = 26;
const durationInterval = 15;

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

export default function ConnectionResultsPlot({
  connections,
  startDateTime,
  navigation,
}) {
  const calculateDurationMinutes = React.useCallback(
    (connection) => {
      const actions = connection.actions;
      const transfers = filterTransfers(actions);
      if (transfers.length > 0) {
        const lastTransfer = transfers[transfers.length - 1];
        const endDateTime = parseDateTime(lastTransfer.end_datetime);
        const durationMillis = endDateTime - startDateTime;
        const durationMinutes = durationMillis / 1000 / 60;
        return durationMinutes;
      } else {
        return actions[0].duration_in_minutes;
      }
    },
    [startDateTime]
  );

  const maxDurationMinutes = React.useMemo(
    () => Math.max(...connections.map(calculateDurationMinutes)),
    [connections]
  );

  const lastMinutes = React.useMemo(
    () =>
      Math.ceil(
        Math.min(Math.max(maxDurationMinutes, 0), 900) / durationInterval
      ) * durationInterval,
    [maxDurationMinutes, durationInterval]
  );

  const height = React.useMemo(() => calculateY(lastMinutes) + 70, [
    lastMinutes,
  ]);

  const handleShow = (connection) => {
    navigation.navigate("ConnectionDetails", { connection: connection });
  };

  let horizontalLines = [];
  for (let minutes = 0; minutes <= lastMinutes; minutes += durationInterval) {
    horizontalLines.push(
      <GridLine
        orientation="horizontal"
        position={calculateY(minutes)}
        icon="clock-outline"
        label={minutes + " min"}
        key={"h" + minutes}
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
        key={"v" + minutes}
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
