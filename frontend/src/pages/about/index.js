import { Title, Container, Main } from '../../components'
import styles from './styles.module.css'
import MetaTags from 'react-meta-tags'

const About = ({ updateOrders, orders }) => {
  
  return <Main>
    <MetaTags>
      <title>О проекте</title>
      <meta name="description" content="Фудграм - О проекте" />
      <meta property="og:title" content="О проекте" />
    </MetaTags>
    
    <Container>
      <h1 className={styles.title}>Привет!</h1>
      <div className={styles.content}>
        <div>
          <h2 className={styles.subtitle}>Что это за сайт?</h2>
          <div className={styles.text}>
            <p className={styles.textItem}>
              Добро пожаловать на Foodgram! Этот проект создан в рамках обучения в Яндекс Практикуме, но является полностью самостоятельной разработкой.
            </p>
            <p className={styles.textItem}>
              Foodgram — это удобная онлайн-платформа для кулинаров всех уровней. Здесь вы можете легко создавать, хранить и делиться своими любимыми рецептами.
            </p>
            <p className={styles.textItem}>
              Наш сайт предлагает множество полезных функций: скачивайте списки необходимых продуктов для любого рецепта, просматривайте кулинарные творения ваших друзей и добавляйте понравившиеся рецепты в избранное, чтобы они всегда были под рукой.
            </p>
            <p className={styles.textItem}>
              Для доступа ко всем возможностям платформы достаточно простой регистрации. Мы не требуем подтверждения электронной почты, так что вы можете использовать любой удобный для вас адрес.
            </p>
            <p className={styles.textItem}>
              Присоединяйтесь к Foodgram и начните делиться своими кулинарными шедеврами уже сегодня!
            </p>
          </div>
        </div>
        <aside>
          <h2 className={styles.additionalTitle}>
            Ссылки
          </h2>
          <div className={styles.text}>
            <p className={styles.textItem}>
              Код проекта находится тут - <a href="https://github.com/Hihi567no/foodgram-st" className={styles.textLink}>Github</a>
            </p>
            <p className={styles.textItem}>
              Автор проекта: <a href="#" className={styles.textLink}>Схрейдер Александр</a>
            </p>
          </div>
        </aside>
      </div>
      
    </Container>
  </Main>
}

export default About

