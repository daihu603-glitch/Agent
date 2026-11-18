#include <linux/module.h>
static int __init x(void){return 0;}
module_init(x);
