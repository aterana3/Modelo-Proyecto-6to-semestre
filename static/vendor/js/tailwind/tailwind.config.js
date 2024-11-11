tailwind.config = {
    theme: {
        extend: {
            colors: {
                'primary': {
                    DEFAULT: '#3a9abf',
                    light: '#00b4c7',
                }
            },
            backgroundImage: {
                'login': "url('/static/images/authentication/login-bg.webp')",
            },
            gridTemplateRows: {
                'layout': 'auto 1fr auto',
            },
        },
    },
}