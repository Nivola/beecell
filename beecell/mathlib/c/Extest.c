#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "Extest.h"

long int fac(int n) {
	if (n < 2) return(1);
	return (n)*fac(n-1);
}

long int fib(int n) {
    if (n < 2) return(1);
    return (fib(n-2) + fib(n-1));
}

char *reverse(char *s) {
	register char t, *p = s, *q = (s + (strlen(s) - 1));

	while (s && (p < q)) {
		t = *p;
		*p++ = *q;
		*q-- = t;
	}
	return s;
}

void countdown(int n) {
	/*printf("number: %d\n", n);*/
	while (n > 0) {
		n--;
	}
}

int test() {
	char s[BUFSIZ];
	printf("4! == %d\n", fac(4));
	printf("8! == %d\n", fac(8));
	printf("12! == %d\n", fac(12));
	strcpy(s, "abcdef");
	printf("reversing 'abcdef', we get '%s'\n", reverse(s));
	strcpy(s, "madam");
	printf("reversing 'madam', we get '%s'\n", reverse(s));
	return 0;
}
