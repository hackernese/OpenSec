<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($title) ?> — Imager</title>
    <link rel="stylesheet" href="/css/app.css">

    <!-- <link rel="icon" href="https://resources.imagesharer.xyz/icon.ico" type="image/png"> -->

    <link rel="icon" href="https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTlZ85k3kCmkla3sPyrD94VIVRwnfCN0BzZjLw5BGf6HQ&s=10" type="image/png">
</head>
<body>

<header class="site-header">
    <a href="/dashboard" class="logo">📷 Imager</a>
    <nav>
        <?php if ($isAuth): ?>
            <a href="/dashboard">My Images</a>
            <a href="/images/upload">Upload</a>
            <a href="/profile">Profile</a>
            <form method="POST" action="/logout" class="inline-form">
                <button type="submit" class="btn-link">Log out</button>
            </form>
        <?php else: ?>
            <a href="/login">Log in</a>
            <a href="/register" class="btn btn-primary btn-sm">Sign up</a>
        <?php endif; ?>
    </nav>
</header>

<main class="container">

    <?php if (!empty($flash['success'])): ?>
        <div class="alert alert-success"><?= htmlspecialchars($flash['success']) ?></div>
    <?php endif; ?>

    <?php if (!empty($flash['error'])): ?>
        <div class="alert alert-error"><?= htmlspecialchars($flash['error']) ?></div>
    <?php endif; ?>

    <?= $content ?>

</main>

<footer class="site-footer">
    <p>Imager &mdash; your images, your control.</p>
</footer>

    <!-- <script src="/js/awsvalid.js"></script> -->


</body>
</html>
