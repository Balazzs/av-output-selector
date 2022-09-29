#pragma comment(lib, "user32")
#include <lowlevelmonitorconfigurationapi.h>
#include <iostream>
#include <vector>
#include <map>
#include <string>
#include <algorithm>

std::wstring GetDeviceName (LUID adapterId, UINT32 targetId)
{
    DISPLAYCONFIG_TARGET_DEVICE_NAME name;
    name.header.type = DISPLAYCONFIG_DEVICE_INFO_GET_TARGET_NAME;
    name.header.size = sizeof (name);
    name.header.adapterId = adapterId;
    name.header.id = targetId;
    DisplayConfigGetDeviceInfo (&name.header);
    return std::wstring (name.monitorFriendlyDeviceName);
}

struct Connection
{
    std::wstring    displayName;
    UINT32          displayId;
};

std::vector<DISPLAYCONFIG_PATH_INFO> GetPathInfoArray ()
{
    UINT32 numPathArrayElements, numModeInfoArrayElements;
    GetDisplayConfigBufferSizes ((QDC_ALL_PATHS), &numPathArrayElements, &numModeInfoArrayElements);
    std::vector<DISPLAYCONFIG_PATH_INFO> pathInfoArray (numPathArrayElements);
    std::vector<DISPLAYCONFIG_MODE_INFO> modeInfoArray (numModeInfoArrayElements);
    QueryDisplayConfig ((QDC_ALL_PATHS), &numPathArrayElements, pathInfoArray.data (), &numModeInfoArrayElements, modeInfoArray.data (), NULL);
    return pathInfoArray;
}

bool IsAlreadyConnected (DISPLAYCONFIG_SOURCE_DEVICE_NAME       sourceName,
                         DISPLAYCONFIG_TARGET_PREFERRED_MODE    preferedMode,
                         const std::vector<Connection>& connections)
{
    return std::any_of (connections.begin (),
                        connections.end (),
                        [&sourceName, &preferedMode] (const Connection& conn) {
                            return conn.displayName == std::wstring (sourceName.viewGdiDeviceName) || conn.displayId == preferedMode.header.id;
                        });
}

void SetConnections (const std::map<std::wstring, bool>& monitorStates)
{
    auto pathInfoArray = GetPathInfoArray ();

    std::vector<Connection> connections;


    DISPLAYCONFIG_SOURCE_DEVICE_NAME sourceName = {};
    sourceName.header.type = DISPLAYCONFIG_DEVICE_INFO_GET_SOURCE_NAME;
    sourceName.header.size = sizeof (sourceName);

    DISPLAYCONFIG_TARGET_PREFERRED_MODE preferedMode = {};
    preferedMode.header.type = DISPLAYCONFIG_DEVICE_INFO_GET_TARGET_PREFERRED_MODE;
    preferedMode.header.size = sizeof (preferedMode);

    int newId = 0;

    for (auto& pathInfo : pathInfoArray) {
        bool match = false;
        sourceName.header.adapterId = pathInfo.sourceInfo.adapterId;
        sourceName.header.id = pathInfo.sourceInfo.id;

        preferedMode.header.adapterId = pathInfo.targetInfo.adapterId;
        preferedMode.header.id = pathInfo.targetInfo.id;

        DisplayConfigGetDeviceInfo (&sourceName.header);
        DisplayConfigGetDeviceInfo (&preferedMode.header);

        std::wstring deviceName = GetDeviceName (pathInfo.targetInfo.adapterId, pathInfo.targetInfo.id);

        if (pathInfo.flags & DISPLAYCONFIG_PATH_ACTIVE || pathInfo.targetInfo.targetAvailable && !IsAlreadyConnected (sourceName, preferedMode, connections)) {
            connections.push_back ({ sourceName.viewGdiDeviceName, preferedMode.header.id });

            if (monitorStates.contains (deviceName)) {
                if (monitorStates.at (deviceName)) {
                    pathInfo.flags |= DISPLAYCONFIG_PATH_ACTIVE;
                } else {
                    pathInfo.flags &= ~DISPLAYCONFIG_PATH_ACTIVE;
                }
            }

            pathInfo.sourceInfo.id = connections.size ();
            pathInfo.targetInfo.id = preferedMode.header.id;
            pathInfo.sourceInfo.modeInfoIdx = DISPLAYCONFIG_PATH_MODE_IDX_INVALID;
            pathInfo.targetInfo.modeInfoIdx = DISPLAYCONFIG_PATH_MODE_IDX_INVALID;
        }
    }

    SetDisplayConfig (pathInfoArray.size (), pathInfoArray.data (), 0, NULL, (SDC_VALIDATE | SDC_TOPOLOGY_SUPPLIED | SDC_ALLOW_PATH_ORDER_CHANGES));
    SetDisplayConfig (pathInfoArray.size (), pathInfoArray.data (), 0, NULL, (SDC_APPLY | SDC_TOPOLOGY_SUPPLIED | SDC_ALLOW_PATH_ORDER_CHANGES));
}


int wmain (int argc, wchar_t** argv)
{
    const bool badArgCount = argc % 2 != 1;
    if (badArgCount) {
        std::cerr << "Wrong input format, give \"monitor_name\" [on|off] values in pairs" << std::endl;
        const bool noArguments = argc == 1;
        return noArguments ? 0 : 1;
    }

    std::map<std::wstring, bool> monitorStates;

    for (int i = 1; i < argc; i += 2) {
        std::wstring state (argv[i + 1]);

        if (state != L"on" && state != L"off") {
            std::wcerr << "Wrong format, each monitor can only be \"on\" or \"off\", not \"" << state << "\"" << std::endl;
            return 1;
        }

        monitorStates[std::wstring (argv[i])] = (state == L"on");
    }

    SetConnections (monitorStates);
}
