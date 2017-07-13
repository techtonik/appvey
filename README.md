Automatically creates AppVeyor project if it doesn't exist for
current git repository URL (uses origin), uploads settings from
local appveyor.yml (always) and kicks build.

Example run for testing https://github.com/techtonik/piglit:
```
> git clone https://github.com/techtonik/piglit
> cd piglit
> pip install appvey
> appvey
techtonik/piglit                 https://github.com/techtonik/piglit
techtonik/augeas                 https://github.com/hercules-team/augeas
techtonik/linkchecker            https://github.com/wummel/linkchecker
techtonik/wheel                  techtonik/wheel
techtonik/testbin                https://github.com/techtonik/testbin
techtonik/hexdump                techtonik/hexdump
techtonik/tox                    techtonik/tox
techtonik/unicode-far            http://svn.code.sf.net/p/farmanager/code/trunk/unicode_far
techtonik/opencv-python          https://github.com/skvark/opencv-python
techtonik/scons                  techtonik/scons
detected: https://github.com/techtonik/piglit
updating: techtonik/piglit
configured techtonik/piglit from appveyor.yml
build started for techtonik/piglit
```
