export default function Health() {
    return <div>OK</div>;
}

export async function getServerSideProps() {
    return {
        props: {},
    };
}
