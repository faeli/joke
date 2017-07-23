#!/usr/bin/env python
# -*- coding: utf-8 -*-


from joke import app, loop

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7315, debug=True)