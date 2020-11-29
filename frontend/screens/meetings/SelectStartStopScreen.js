import * as React from "react";
import { updateMembershipStopName } from "../../api/MeetingsApi";
import NearestStopsMap from "../../components/NearestStopsMap";

export default function SelectStartStopScreen({ navigation, route }) {
  const userUuid = route.params.userUuid;
  const meetingUuid = route.params.meetingUuid;

  const handleSelect = async (stop) => {
    await updateMembershipStopName({
      meetingUuid,
      userUuid,
      stopName: stop.name,
    });
    navigation.pop();
  };

  return <NearestStopsMap onSelect={handleSelect} />;
}
