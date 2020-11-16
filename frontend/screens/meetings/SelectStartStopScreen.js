import * as React from "react";
import { updateMeetingMemberStopName } from "../../api/MeetingsApi";
import NearestStopsMap from "../../components/NearestStopsMap";

export default function SelectStartStopScreen({ navigation, route }) {
  const userUuid = route.params.userUuid;
  const meetingUuid = route.params.meetingUuid;

  const handleSelect = async (stop) => {
    await updateMeetingMemberStopName(meetingUuid, userUuid, stop.name);
    navigation.pop();
  };

  const handleClose = () => {
    navigation.pop();
  };

  return <NearestStopsMap onSelect={handleSelect} onClose={handleClose} />;
}
