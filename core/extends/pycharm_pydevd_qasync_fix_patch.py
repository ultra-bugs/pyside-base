#              M""""""""`M            dP
#              Mmmmmm   .M            88
#              MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#              MMP  .MMMMM  88    88  88888"    88'  `88
#              M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#              M         M  `88888P'  dP   `YP  `88888P'
#              MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#              * * * * * * * * * * * * * * * * * * * * *
#              * -    - -   F.R.E.E.M.I.N.D   - -    - *
#              * -  Copyright © 2026 (Z) Programing  - *
#              *    -  -  All Rights Reserved  -  -    *
#              * * * * * * * * * * * * * * * * * * * * *

import sys
import asyncio
import qasync


# ======================================================================
# BẢN VÁ DÀNH RIÊNG CHO PYCHARM DEBUGGER KHI KẾT HỢP VỚI QASYNC
# (Tránh lỗi: TypeError: callback must be callable: Task)
# ======================================================================
def patch_qasync_for_pycharm_debugger():
    # Lấy class QEventLoop của qasync
    loop_class = getattr(qasync, '_QEventLoop', qasync.QEventLoop)
    if hasattr(loop_class, '_isCallLaterPatched'):
        return
    original_call_later = loop_class.call_later

    def _patched_call_later(self, delay, callback, *args, context=None):
        # Nếu callback KHÔNG call được (do PyCharm nhét Task object vào)
        if not callable(callback):
            # Moi móc hàm chạy thực sự của Task ra (_Task__step là hàm chuẩn của cPython)
            if hasattr(callback, '_Task__step'):
                callback = callback._Task__step
            elif hasattr(callback, '_step'):
                callback = callback._step

        # Trả lại cho qasync chạy bình thường
        return original_call_later(self, delay, callback, *args, context=context)

    # Đè thẳng vào core của qasync
    loop_class.call_later = _patched_call_later
    loop_class._isCallLaterPatched = True



# Chạy bản vá ngay lập tức
patch_qasync_for_pycharm_debugger()
# ======================================================================

