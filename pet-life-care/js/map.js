function getLocation(){

 navigator.geolocation.getCurrentPosition(
  position => {

   const lat = position.coords.latitude;
   const lng = position.coords.longitude;

   console.log(lat,lng);

  }
 );

}