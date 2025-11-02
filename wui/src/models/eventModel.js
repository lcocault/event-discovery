export class Event {
  constructor(id, name, startTime, endTime, latitude, longitude) {
    this.id = id;
    this.name = name;
    this.startTime = startTime;
    this.endTime = endTime;
    this.latitude = latitude;
    this.longitude = longitude;
  }

  static fromApiResponse(apiResponse) {
    return new Event(
      apiResponse.id,
      apiResponse.name,
      apiResponse.start_time,
      apiResponse.end_time,
      apiResponse.latitude,
      apiResponse.longitude
    );
  }
}