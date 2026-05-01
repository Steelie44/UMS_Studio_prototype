#include "ums_protocol.h"
#include "ums_dispatch.h"
#include "ums_state.h"

static uint16_t last_seq = 0;

void ums_dispatch(const ums_packet_t* p) {
    last_seq = p->seq;

    switch (p->type) {
        case UMS_TYPE_MOVE:
            ums_exec_move(p);
            break;
        case UMS_TYPE_ARC:
            ums_exec_arc(p);
            break;
        case UMS_TYPE_DWELL:
            ums_exec_dwell(p);
            break;
        case UMS_TYPE_SPINDLE:
            ums_exec_spindle(p);
            break;
        case UMS_TYPE_COOLANT:
            ums_exec_coolant(p);
            break;
        case UMS_TYPE_SYSTEM:
            ums_exec_system(p);
            break;
    }
}
