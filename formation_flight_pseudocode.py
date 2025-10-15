-- MASTER NODE

function master_main()
    print("Connecting to MAVProxy on port 16000...")
    connect_to_mavproxy()
    start_heartbeat_thread()

    while true do
        gps = read_GLOBAL_POSITION_INT()
        if gps then
            lat, lon, alt = gps.lat, gps.lon, gps.alt
            write_to_file("shared_gps.txt", lat, lon, alt)
            print(string.format("MASTER → LAT=%.6f LON=%.6f ALT=%.1f", lat, lon, alt))
        else
            print("No GPS message received")
        end
        sleep(0.2)
    end
end


-- SLAVE NODE

function slave_main()
    -- Configuration
    SLAVE_PORTS = {14330, 14440, 14660, 14770}
    TAKEOFF_ALT = 10
    OFFSET = 100      -- meters per index

    for i, port in ipairs(SLAVE_PORTS) do
        spawn_thread(drone_thread, port, "DRONE-"..i, i)
    end

    while true do sleep(5) end
end


-- Each slave runs in its own thread
function drone_thread(port, name, index)
    vehicle = connect("udpin:127.0.0.1:"..port)
    wait_for_heartbeat(vehicle)
    set_mode(vehicle, "GUIDED")
    arm_and_takeoff(vehicle, TAKEOFF_ALT)

    while true do
        gps_master = read_shared_gps()
        if gps_master == nil then
            sleep(0.1)
        else
            -- Calculate offset longitude (100 m × index)
            lon_offset = apply_offset(gps_master.lat, gps_master.lon, OFFSET * index)

            -- Send waypoint command
            send_waypoint(vehicle, gps_master.lat, lon_offset, gps_master.alt)

            -- Wait until within threshold
            repeat
                pos = get_current_position(vehicle)
                dist = distance(pos, {gps_master.lat, lon_offset})
                alt_err = abs(pos.alt - gps_master.alt)
                print(string.format("[%s] DIST=%.2fm ALT_ERR=%.2fm", name, dist, alt_err))
                sleep(0.1)
            until dist < 1.0 and alt_err < 0.8
        end
    end
end


-- SUPPORT FUNCTIONS

function send_waypoint(vehicle, lat, lon, alt)
    cmd = MAVLink_mission_item_int_message(
        frame = GLOBAL_RELATIVE_ALT,
        command = MAV_CMD_NAV_WAYPOINT,
        x = lat * 1e7,
        y = lon * 1e7,
        z = alt,
        current = 2
    )
    vehicle.mav.send(cmd)
end

function apply_offset(lat, lon, offset_m)
    -- Adjust longitude based on offset distance and latitude
    dlon = offset_m / (6378137 * cos(rad(lat)))
    return lon + deg(dlon)
end

function arm_and_takeoff(vehicle, alt)
    send_arm_command(vehicle)
    wait_until_armed(vehicle)
    send_takeoff_command(vehicle, alt)
    wait_until_altitude_reached(vehicle, alt)
end

-- Entry point

arg = sys.argv[1]
if arg == "master" then
    master_main()
elseif arg == "slave" then
    slave_main()
else
    print("Usage: python3 swarm.py [master|slave]")
end
