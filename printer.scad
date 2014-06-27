laser_base_point = [-3.0,18.0,-70.0];
laser_look_at = [0.0,18.0,-70.0];

mirror1_base_point=[15.0,18.0,-70];
mirror1_look_at=[-1.0, 1.0, 0.0]+mirror1_base_point;
deflection1 = -30;

mirror2_base_point=[15.0,25.0,-70];
mirror2_look_at=[ 0.0,-1.0,-1.0]+mirror2_base_point;

module peachy_mirror(base_point,look_at) {
    translate(base_point){
        rotate(to_polar(base_point,look_at)){
          rotate([180 ,0,0]){
              cube([10,5,0.01], center = true);
          }

        }
    }
}

function vec_to_polar(dx,dy,dz) = [0 , acos(dz / sqrt(dx*dx + dy*dy + dz*dz)), atan2(dy,dx)];

function to_polar(base_point,look_at) = vec_to_polar(
    look_at[0] - base_point[0],
    look_at[1] - base_point[1],
    look_at[2] - base_point[2]
    );


module laser_beam(base_point,look_at) {
    translate(base_point){
        rotate(to_polar(base_point,look_at)){
              cylinder(h=25, r=0.8);
        }
    }
    
    translate(mirror1_base_point)
        //rotate(to_polar(mirror1_base_point,mirror1_look_at))
          mirror(mirror1_look_at-mirror1_base_point)
          rotate([180 ,0,0])
            rotate(to_polar(base_point,look_at))
              cylinder(h=70, r=0.8);

}

module laser(base_point,look_at) {
    translate(base_point){
        rotate(to_polar(base_point,look_at)){
              rotate([180,0,0]){
                  cylinder(h =50, r =5);
           }
        }
    }
}



color("grey")
laser(laser_base_point, laser_look_at);

color("blue")
laser_beam(laser_base_point, laser_look_at);

color("green")
  peachy_mirror(mirror1_base_point,mirror1_look_at);


color("red")
  peachy_mirror(mirror2_base_point,mirror2_look_at);


color("green")
translate(laser_base_point){
    sphere(1);
}

color("red")
translate(laser_look_at){
    sphere(1);
}
