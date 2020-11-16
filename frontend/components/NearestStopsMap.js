import * as React from "react";
import * as Location from "expo-location";
import { Alert } from "react-native";
import MapView, { Marker } from "react-native-maps";
import { IconButton } from "react-native-paper";
import { getStops } from "../api/ConnectionsApi";
import { getDistance, orderByDistance } from "geolib";

const initialRegion = {
  latitude: 50.04,
  longitude: 19.96,
  latitudeDelta: 0.3,
  longitudeDelta: 0.4,
};

const padding = {
  top: 100,
  bottom: 100,
  left: 100,
  right: 100,
};

const threshold = 1000; // in metres

export default function NearestStopsMap({ onSelect, onClose }) {
  const [location, setLocation] = React.useState(null);
  const [nearestStops, setNearestStops] = React.useState([]);

  const mapRef = React.useRef(null);

  React.useEffect(() => {
    (async () => {
      let { status } = await Location.requestPermissionsAsync();
      if (status !== "granted") {
        Alert.alert("Wystąpił błąd", "Brak uprawnień");
        return;
      }

      let location = await Location.getCurrentPositionAsync({});
      setLocation(location);
    })();
  }, []);

  const getNearestStops = async (origin) => {
    const stops = await getStops();
    // return stops.filter((stop) => getDistance(origin, stop) < threshold);
    return orderByDistance(origin, stops).slice(0, 10);
  };

  const showNearestStops = async () => {
    if (!location) {
      setNearestStops([]);
      return;
    }
    const nearestStops = await getNearestStops(location.coords);
    setNearestStops(nearestStops);
    fitToContents([...nearestStops, location.coords]);
  };

  const fitToContents = (coords) => {
    mapRef.current.fitToCoordinates(coords, {
      animated: true,
      edgePadding: padding,
    });
  };

  React.useEffect(() => {
    showNearestStops();
  }, [location]);

  return (
    <>
      {onClose && (
        <IconButton
          icon="close"
          style={{ position: "absolute", right: 4, top: -50, zIndex: 3 }}
          onPress={() => onClose()}
        />
      )}
      <MapView
        ref={mapRef}
        initialRegion={initialRegion}
        maxZoomLevel={18}
        showsUserLocation={true}
        moveOnMarkerPress={false}
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 0,
          bottom: 0,
          zIndex: 2,
        }}
      >
        {nearestStops.map((stop, i) => (
          <Marker
            key={i}
            coordinate={stop}
            onPress={onSelect ? () => onSelect(stop) : null}
          />
        ))}
      </MapView>
    </>
  );
}
