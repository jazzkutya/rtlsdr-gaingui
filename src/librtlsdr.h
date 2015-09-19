/*
 * rtl-sdr, turns your Realtek RTL2832 based DVB dongle into a SDR receiver
 * Copyright (C) 2012-2013 by Steve Markgraf <steve@steve-m.de>
 * Copyright (C) 2012 by Dimitri Stolnikov <horiz0n@gmx.net>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#ifndef __LIBRTLSDR_H
#define __LIBRTLSDR_H

#ifdef __cplusplus
extern "C" {
#endif

#include <libusb.h>
#include "tuner_e4k.h"
#include "tuner_fc0012.h"
#include "tuner_fc0013.h"
#include "tuner_fc2580.h"
#include "tuner_r82xx.h"

typedef struct rtlsdr_tuner_iface {
    /* tuner interface */
    int (*init)(void *);
    int (*exit)(void *);
    int (*set_freq)(void *, uint32_t freq /* Hz */);
    int (*set_bw)(void *, int bw /* Hz */);
    int (*set_gain)(void *, int gain /* tenth dB */);
    int (*set_if_gain)(void *, int stage, int gain /* tenth dB */);
    int (*set_gain_mode)(void *, int manual);
} rtlsdr_tuner_iface_t;

enum rtlsdr_async_status {
    RTLSDR_INACTIVE = 0,
    RTLSDR_CANCELING,
    RTLSDR_RUNNING
};

#define FIR_LEN 16

struct rtlsdr_dev {
	libusb_context *ctx;
	struct libusb_device_handle *devh;
	uint32_t xfer_buf_num;
	uint32_t xfer_buf_len;
	struct libusb_transfer **xfer;
	unsigned char **xfer_buf;
	rtlsdr_read_async_cb_t cb;
	void *cb_ctx;
	enum rtlsdr_async_status async_status;
	int async_cancel;
	/* rtl demod context */
	uint32_t rate; /* Hz */
	uint32_t rtl_xtal; /* Hz */
	int fir[FIR_LEN];
	int direct_sampling;
	/* tuner context */
	enum rtlsdr_tuner tuner_type;
	rtlsdr_tuner_iface_t *tuner;
	uint32_t tun_xtal; /* Hz */
	uint32_t freq; /* Hz */
	uint32_t bw;
	uint32_t offs_freq; /* Hz */
	int corr; /* ppm */
	int gain; /* tenth dB */
	struct e4k_state e4k_s;
	struct r82xx_config r82xx_c;
	struct r82xx_priv r82xx_p;
	/* status */
	int dev_lost;
	int driver_active;
	unsigned int xfer_errors;
    rtlsdr_mmif_t *mmif;
};

#ifdef __cplusplus
}
#endif

#endif /* __RTL_SDR_H */
