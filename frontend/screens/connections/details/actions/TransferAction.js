import * as React from "react";
import { Text, List } from "react-native-paper";
import DelayText from "../../../../components/DelayText";
import { parseDateTime, formatTime } from "../../../../utils";

export default function TransferAction({ transfer }) {
  const startDateTime = parseDateTime(transfer.start_datetime);
  const endDateTime = parseDateTime(transfer.end_datetime);

  const startStopName = transfer.start_stop_name;
  const endStopName = transfer.end_stop_name;

  const delay = transfer.delay;

  const title = (
    <Text>
      {transfer.route_name}&nbsp;&rarr;&nbsp;{transfer.headsign}
    </Text>
  );
  const description = (
    <React.Fragment>
      {formatTime(startDateTime)}
      <DelayText delay={delay} /> {startStopName}
      {"\n"}
      {formatTime(endDateTime)}
      <DelayText delay={delay} /> {endStopName}
    </React.Fragment>
  );

  const icon = transfer.route_name.length == 3 ? "bus" : "tram";

  return (
    <List.Item
      title={title}
      description={description}
      left={(props) => (
        <List.Icon {...props} icon={icon} style={{ margin: 0 }} />
      )}
      style={{ paddingLeft: 0, paddingRight: 0 }}
    />
  );
}
