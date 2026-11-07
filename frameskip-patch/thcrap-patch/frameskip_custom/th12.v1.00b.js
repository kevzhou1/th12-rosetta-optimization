{
	"codecaves": {
		"fs_acc": {
			"access": "rw",
			"size": 4
		},
		"fs_ticks": {
			"access": "rw",
			"size": 4
		},
		"fs_meter": {
			"access": "rw",
			"size": 4
		},
		"fs_decide": {
			"access": "re",
			"code": "fe4514 a1<codecave:fs_acc> 83c002 83f803 7223 83e803 a3<codecave:fs_acc> 8b0d<codecave:fs_ticks> 890d<codecave:fs_meter> c705<codecave:fs_ticks>00000000 e9[Rx50500] a3<codecave:fs_acc> ff05<codecave:fs_ticks> e9[Rx50566]"
		}
	},
	"binhacks": {
		"fs_render_decision": {
			"title": "Custom frameskip: render N of every M frames (timer-paced loop)",
			"addr": "0x4504eb",
			"expected": "fe4514 8a4514 0fb60dceea4c00 0fbed0 41 3bca 7f66",
			"code": "e9[codecave:fs_decide] <nop:16>"
		},
		"fs_force_timer_loop": {
			"title": "Custom frameskip: always use the timer-paced frame loop (never the vsync-paced one)",
			"addr": "0x44f88e",
			"expected": "7515",
			"code": "eb15"
		},
		"fs_fps_meter": {
			"title": "Custom frameskip: FPS meter and replay slowdown stat count skipped frames",
			"addr": "0x41cc5c",
			"expected": "0fb60dceea4c00",
			"code": "8b0d<codecave:fs_meter> 90"
		}
	}
}
